## ADDED Requirements

### Requirement: AWS ECR Registry Authentication
The Kubernetes cluster SHALL authenticate with AWS ECR to pull container images from private repositories using stored credentials.

#### Scenario: Secret exists in cluster
- **WHEN** kubectl get secret ecr-registry is executed
- **THEN** a Secret of type kubernetes.io/dockerconfigjson exists in the default namespace

#### Scenario: ServiceAccount has ImagePullSecret
- **WHEN** kubectl get serviceaccount default -o yaml is executed
- **THEN** the ServiceAccount includes ecr-registry in its imagePullSecrets

#### Scenario: Pod can pull from private ECR
- **WHEN** A pod is created with an image from private ECR (e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest)
- **THEN** The image pull succeeds using credentials from the ecr-registry secret

### Requirement: Environment-based Credential Management
The system SHALL support reading AWS credentials from environment variables during manifest deployment.

#### Scenario: Manifest uses envsubst placeholders
- **WHEN** The manifest files contain placeholders like ${AWS_ACCESS_KEY_ID}
- **THEN** Running envsubst produces a valid manifest with substituted values

#### Scenario: Missing credentials fail at apply time
- **WHEN** kubectl apply is run without providing AWS credentials
- **THEN** The apply fails or produces an invalid secret without valid base64 data

### Requirement: .env-example documents required variables
The .env-example file SHALL document all required AWS credentials needed for ECR authentication.

#### Scenario: User checks .env-example
- **WHEN** A user reviews the .env-example file
- **THEN** They can see all required environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ACCOUNT_ID, AWS_REGION

#### Scenario: .env-example has placeholder values
- **WHEN** .env-example is created
- **THEN** It contains placeholder values (e.g., "your-access-key-here") with comments indicating they must be replaced