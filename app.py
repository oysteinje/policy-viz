from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import PolicyClient

def get_policy_assignments(credential, subscription_id):
    try:
        # Create policy client for this subscription
        policy_client = PolicyClient(credential, subscription_id)

        # List policy assignments at subscription scope
        assignments = policy_client.policy_assignments.list()

        print("\nPolicy Assignments:")
        for assignment in assignments:
            print(f"\nPolicy Name: {assignment.name}")
            print(f"Display Name: {assignment.display_name}")
            print(f"Description: {assignment.description}")
            print(f"Enforcement Mode: {assignment.enforcement_mode}")
            print("-" * 50)

    except Exception as e:
        print(f"Error getting policy assignments: {str(e)}")

def get_azure_subscriptions():
    try:
        # Create credential object
        credential = DefaultAzureCredential()

        # Create subscription client
        subscription_client = SubscriptionClient(credential)

        # List subscriptions
        subscriptions = subscription_client.subscriptions.list()

        print("\nSubscriptions found in your Azure account:\n")
        for sub in subscriptions:
            print(f"Name: {sub.display_name}")
            print(f"ID: {sub.subscription_id}")
            print(f"State: {sub.state}")
            print("-" * 50)

            # Get policy assignments for each subscription
            print(f"\nFetching policy assignments for subscription: {sub.display_name}")
            get_policy_assignments(credential, sub.subscription_id)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    print("Connecting to Azure...")
    get_azure_subscriptions()
