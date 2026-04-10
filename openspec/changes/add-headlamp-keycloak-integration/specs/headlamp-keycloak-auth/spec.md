## ADDED Requirements

### Requirement: Headlamp authenticates via Keycloak OIDC
The system SHALL authenticate Headlamp users through Keycloak OIDC using the master realm.

#### Scenario: OIDC login flow
- **WHEN** user navigates to Headlamp and clicks "Sign in"
- **THEN** user is redirected to Keycloak login page
- **AND** after successful authentication, user is redirected back to Headlamp

### Requirement: Headlamp uses OIDC impersonation
The system SHALL validate OIDC tokens and impersonate the authenticated user when making Kubernetes API calls.

#### Scenario: API request with impersonation
- **WHEN** authenticated OIDC user views cluster resources
- **THEN** Headlamp sends requests with Impersonate-User header set to the OIDC user's identity

### Requirement: OIDC credentials stored in secret
The system SHALL store OIDC client credentials in a Kubernetes secret.

#### Scenario: Secret contains required fields
- **WHEN** headlamp-oidc-secret is created
- **THEN** it contains OIDC_CLIENT_ID, OIDC_CLIENT_SECRET, and OIDC_ISSUER_URL

### Requirement: Keycloak client automatically configured
The system SHALL create the Headlamp OIDC client in Keycloak master realm during bootstrap.

#### Scenario: Client created with correct settings
- **WHEN** run-all.sh completes
- **THEN** Keycloak has client "headlamp" with correct redirect URIs and scopes