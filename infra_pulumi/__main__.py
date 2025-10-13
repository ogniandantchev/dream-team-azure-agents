import pulumi
import pulumi_azure_native as azure_native
import pulumi_azuread as azuread
from pulumi import Config, ResourceOptions, Output
import json
import base64

# Configuration
config = Config()
environment_name = config.require("environmentName")
location = config.get("location") or "eastus"
principal_id = config.require("principalId")

# Tags
tags = {
    "azd-env-name": environment_name,
    "framework": "microsoft-agent-framework",
    "frontend": "streamlit", 
    "infrastructure": "pulumi"
}

# Generate a resource token for unique naming
resource_token = pulumi.get_stack().lower()[:10]
prefix = "dreamv2"

# Resource Group
resource_group = azure_native.resources.ResourceGroup(
    "rg",
    resource_group_name=f"rg-{environment_name}",
    location=location,
    tags=tags
)

# Log Analytics Workspace
log_analytics = azure_native.operationalinsights.Workspace(
    "log-analytics",
    resource_group_name=resource_group.name,
    workspace_name=f"log-{resource_token}",
    location=location,
    tags=tags,
    sku=azure_native.operationalinsights.WorkspaceSkuArgs(
        name=azure_native.operationalinsights.WorkspaceSkuNameEnum.PERGB2018
    ),
    retention_in_days=30
)

# Application Insights
app_insights = azure_native.insights.Component(
    "app-insights",
    resource_group_name=resource_group.name,
    resource_name=f"appi-{resource_token}",
    location=location,
    tags=tags,
    kind="web",
    application_type=azure_native.insights.ApplicationType.WEB,
    workspace_resource_id=log_analytics.id
)

# Container Registry
container_registry = azure_native.containerregistry.Registry(
    "container-registry",
    resource_group_name=resource_group.name,
    registry_name=f"cr{resource_token}",
    location=location,
    tags=tags,
    sku=azure_native.containerregistry.SkuArgs(
        name=azure_native.containerregistry.SkuName.BASIC
    ),
    admin_user_enabled=True
)

# Key Vault
key_vault = azure_native.keyvault.Vault(
    "key-vault",
    resource_group_name=resource_group.name,
    vault_name=f"kv-{resource_token}",
    location=location,
    tags=tags,
    properties=azure_native.keyvault.VaultPropertiesArgs(
        tenant_id=azure_native.authorization.get_client_config().tenant_id,
        sku=azure_native.keyvault.SkuArgs(
            family="A",
            name=azure_native.keyvault.SkuName.STANDARD
        ),
        access_policies=[
            azure_native.keyvault.AccessPolicyEntryArgs(
                tenant_id=azure_native.authorization.get_client_config().tenant_id,
                object_id=principal_id,
                permissions=azure_native.keyvault.PermissionsArgs(
                    keys=["get", "list", "create", "delete", "update"],
                    secrets=["get", "list", "set", "delete"],
                    certificates=["get", "list", "create", "delete", "update"]
                )
            )
        ]
    )
)

# Storage Account
storage_account = azure_native.storage.StorageAccount(
    "storage-account",
    resource_group_name=resource_group.name,
    account_name=f"st{resource_token}",
    location=location,
    tags=tags,
    sku=azure_native.storage.SkuArgs(
        name=azure_native.storage.SkuName.STANDARD_LRS
    ),
    kind=azure_native.storage.Kind.STORAGE_V2,
    allow_blob_public_access=False
)

# Cosmos DB Account
cosmos_account = azure_native.documentdb.DatabaseAccount(
    "cosmos-account",
    resource_group_name=resource_group.name,
    account_name=f"cosmos-{resource_token}",
    location=location,
    tags=tags,
    database_account_offer_type=azure_native.documentdb.DatabaseAccountOfferType.STANDARD,
    locations=[
        azure_native.documentdb.LocationArgs(
            location_name=location,
            failover_priority=0
        )
    ],
    consistency_policy=azure_native.documentdb.ConsistencyPolicyArgs(
        default_consistency_level=azure_native.documentdb.DefaultConsistencyLevel.SESSION
    ),
    capabilities=[
        azure_native.documentdb.CapabilityArgs(
            name="EnableServerless"
        )
    ]
)

# Cosmos DB Database
cosmos_database = azure_native.documentdb.SqlDatabase(
    "cosmos-database",
    resource_group_name=resource_group.name,
    account_name=cosmos_account.name,
    database_name="chat_database",
    resource=azure_native.documentdb.SqlDatabaseResourceArgs(
        id="chat_database"
    )
)

# Azure OpenAI Service
openai_service = azure_native.cognitiveservices.Account(
    "openai-service",
    resource_group_name=resource_group.name,
    account_name=f"openai-{resource_token}",
    location=location,
    tags=tags,
    kind="OpenAI",
    sku=azure_native.cognitiveservices.SkuArgs(
        name="S0"
    ),
    properties=azure_native.cognitiveservices.AccountPropertiesArgs(
        custom_sub_domain_name=f"{prefix}-{resource_token}",
        public_network_access=azure_native.cognitiveservices.PublicNetworkAccess.ENABLED
    )
)

# OpenAI Model Deployments
gpt4_deployment = azure_native.cognitiveservices.Deployment(
    "gpt4-deployment",
    resource_group_name=resource_group.name,
    account_name=openai_service.name,
    deployment_name="gpt-4o",
    properties=azure_native.cognitiveservices.DeploymentPropertiesArgs(
        model=azure_native.cognitiveservices.DeploymentModelArgs(
            format="OpenAI",
            name="gpt-4o",
            version="2024-05-13"
        ),
        sku=azure_native.cognitiveservices.SkuArgs(
            name="Standard",
            capacity=10
        )
    )
)

embedding_deployment = azure_native.cognitiveservices.Deployment(
    "embedding-deployment",
    resource_group_name=resource_group.name,
    account_name=openai_service.name,
    deployment_name="text-embedding-ada-002",
    properties=azure_native.cognitiveservices.DeploymentPropertiesArgs(
        model=azure_native.cognitiveservices.DeploymentModelArgs(
            format="OpenAI", 
            name="text-embedding-ada-002",
            version="2"
        ),
        sku=azure_native.cognitiveservices.SkuArgs(
            name="Standard",
            capacity=10
        )
    ),
    opts=ResourceOptions(depends_on=[gpt4_deployment])
)

# AI Search Service
ai_search = azure_native.search.SearchService(
    "ai-search",
    resource_group_name=resource_group.name,
    search_service_name=f"search-{resource_token}",
    location=location,
    tags=tags,
    sku=azure_native.search.SkuArgs(
        name=azure_native.search.SkuName.BASIC
    ),
    replica_count=1,
    partition_count=1
)

# Virtual Network
vnet = azure_native.network.VirtualNetwork(
    "vnet",
    resource_group_name=resource_group.name,
    virtual_network_name=f"vnet-{resource_token}",
    location=location,
    tags=tags,
    address_space=azure_native.network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"]
    ),
    subnets=[
        azure_native.network.SubnetArgs(
            name="default",
            address_prefix="10.0.1.0/24"
        ),
        azure_native.network.SubnetArgs(
            name="aca-subnet",
            address_prefix="10.0.2.0/23",
            delegations=[
                azure_native.network.DelegationArgs(
                    name="Microsoft.App/environments",
                    service_name="Microsoft.App/environments"
                )
            ]
        )
    ]
)

# Container Apps Environment
aca_environment = azure_native.app.ManagedEnvironment(
    "aca-environment",
    resource_group_name=resource_group.name,
    environment_name=f"aca-env-{resource_token}",
    location=location,
    tags=tags,
    app_logs_configuration=azure_native.app.AppLogsConfigurationArgs(
        destination="log-analytics",
        log_analytics_configuration=azure_native.app.LogAnalyticsConfigurationArgs(
            customer_id=log_analytics.customer_id,
            shared_key=log_analytics.primary_shared_key
        )
    ),
    vnet_configuration=azure_native.app.VnetConfigurationArgs(
        infrastructure_subnet_id=vnet.subnets.apply(
            lambda subnets: next(s.id for s in subnets if s.name == "aca-subnet")
        )
    )
)

# Communication Services
communication_service = azure_native.communication.CommunicationService(
    "communication-service",
    resource_group_name=resource_group.name,
    communication_service_name=f"comm-{resource_token}",
    location="global",
    tags=tags,
    data_location="United States"
)

email_service = azure_native.communication.EmailService(
    "email-service",
    resource_group_name=resource_group.name,
    email_service_name=f"email-{resource_token}",
    location="global",
    tags=tags,
    data_location="United States"
)

# User Assigned Managed Identity for Container Apps
managed_identity = azure_native.managedidentity.UserAssignedIdentity(
    "managed-identity",
    resource_group_name=resource_group.name,
    resource_name=f"mi-backend-{resource_token}",
    location=location,
    tags=tags
)

# Assign roles to the managed identity
# OpenAI Contributor role
openai_role_assignment = azure_native.authorization.RoleAssignment(
    "openai-role-assignment",
    principal_id=managed_identity.principal_id,
    principal_type=azure_native.authorization.PrincipalType.SERVICE_PRINCIPAL,
    role_definition_id="/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/a001fd3d-188f-4b5d-821b-7da978bf7442".format(
        azure_native.authorization.get_client_config().subscription_id
    ),
    scope=openai_service.id
)

# Cosmos DB Contributor role
cosmos_role_assignment = azure_native.authorization.RoleAssignment(
    "cosmos-role-assignment",
    principal_id=managed_identity.principal_id,
    principal_type=azure_native.authorization.PrincipalType.SERVICE_PRINCIPAL,
    role_definition_id="/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-0000-0000-000000000002".format(
        azure_native.authorization.get_client_config().subscription_id
    ),
    scope=cosmos_account.id
)

# Container App for Backend
backend_container_app = azure_native.app.ContainerApp(
    "backend-container-app",
    resource_group_name=resource_group.name,
    container_app_name="backend",
    location=location,
    tags=tags,
    managed_environment_id=aca_environment.id,
    identity=azure_native.app.ManagedServiceIdentityArgs(
        type=azure_native.app.ManagedServiceIdentityType.USER_ASSIGNED,
        user_assigned_identities={
            managed_identity.id: {}
        }
    ),
    configuration=azure_native.app.ConfigurationArgs(
        ingress=azure_native.app.IngressArgs(
            external=True,
            target_port=8000,
            traffic=[
                azure_native.app.TrafficWeightArgs(
                    weight=100,
                    latest_revision=True
                )
            ]
        ),
        registries=[
            azure_native.app.RegistryCredentialsArgs(
                server=container_registry.login_server,
                identity=managed_identity.id
            )
        ]
    ),
    template=azure_native.app.TemplateArgs(
        containers=[
            azure_native.app.ContainerArgs(
                name="backend",
                image=pulumi.Output.concat(container_registry.login_server, "/backend:latest"),
                env=[
                    azure_native.app.EnvironmentVarArgs(
                        name="AZURE_OPENAI_ENDPOINT",
                        value=openai_service.endpoint
                    ),
                    azure_native.app.EnvironmentVarArgs(
                        name="COSMOS_DB_URI",
                        value=cosmos_account.document_endpoint
                    ),
                    azure_native.app.EnvironmentVarArgs(
                        name="AZURE_SEARCH_SERVICE_ENDPOINT",
                        value=pulumi.Output.concat("https://", ai_search.name, ".search.windows.net/")
                    )
                ],
                resources=azure_native.app.ContainerResourcesArgs(
                    cpu=1.0,
                    memory="2Gi"
                )
            )
        ],
        scale=azure_native.app.ScaleArgs(
            min_replicas=1,
            max_replicas=10
        )
    ),
    opts=ResourceOptions(depends_on=[openai_role_assignment, cosmos_role_assignment])
)

# Static Web App for Frontend (Streamlit)
static_web_app = azure_native.web.StaticSite(
    "static-web-app",
    resource_group_name=resource_group.name,
    name=f"swa-{resource_token}",
    location="West Europe",  # Static Web Apps have limited regions
    tags=tags,
    sku=azure_native.web.SkuDescriptionArgs(
        name="Free",
        tier="Free"
    ),
    build_properties=azure_native.web.StaticSiteBuildPropertiesArgs(
        app_location="/",
        app_build_command="pip install -r requirements.txt",
        output_location="/"
    )
)

# Export important values
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("backend_url", pulumi.Output.concat("https://", backend_container_app.configuration.ingress.fqdn))
pulumi.export("frontend_url", static_web_app.default_hostname.apply(lambda hostname: f"https://{hostname}"))
pulumi.export("azure_openai_endpoint", openai_service.endpoint)
pulumi.export("cosmos_db_uri", cosmos_account.document_endpoint)
pulumi.export("ai_search_endpoint", pulumi.Output.concat("https://", ai_search.name, ".search.windows.net/"))
pulumi.export("container_registry_login_server", container_registry.login_server)
pulumi.export("key_vault_uri", key_vault.properties.vault_uri)
pulumi.export("managed_identity_client_id", managed_identity.client_id)
pulumi.export("communication_service_endpoint", communication_service.host_name)
pulumi.export("application_insights_connection_string", app_insights.connection_string)