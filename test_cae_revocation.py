import base64
import json
import requests
import time
import logging

from azure.identity import InteractiveBrowserCredential, SharedTokenCacheCredential
from azure.mgmt.resource.subscriptions import SubscriptionClient

logging.basicConfig(level=logging.DEBUG)
# Disable redacted logs from ARMHttpLoggingPolicy
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.CRITICAL)


ARM_SCOPE = "https://management.azure.com/.default"
ARM_URL = "https://eastus2euap.management.azure.com/"  # ARM canary
TENANT_ID = "54826b22-38d6-4fb2-bad9-b7b93a3e9c5a"  # azuresdkteam.onmicrosoft.com


def test_cae(credential):
    print("testing CAE with " + credential.__class__.__name__)
    # Enable NetworkTraceLoggingPolicy by setting logging_enable
    client = SubscriptionClient(credential, base_url=ARM_URL, logging_enable=True)

    # verify the credential can get a valid access token
    list(client.subscriptions.list())
    first_token = credential.get_token(ARM_SCOPE)
    print("acquired access token for ARM:")
    print(first_token.token)

    # verify it's a CAE token, i.e. that it can be revoked
    _, payload, _ = first_token.token.split(".")
    decoded_payload = base64.urlsafe_b64decode(payload + "==").decode()
    parsed_payload = json.loads(decoded_payload)
    assert (  # ssm == Smart Session Management
        parsed_payload.get("xms_ssm") == "1"
    ), "CAE isn't enabled for the tenant or user, or MSAL didn't claim client capability CP1"

    # revoking the user's sessions will revoke access and refresh tokens
    graph_token = credential.get_token("User.ReadWrite")
    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/revokeSignInSessions",
        headers={"Authorization": "Bearer " + graph_token.token},
    )
    response.raise_for_status()
    print("revoked user's sessions")

    print("waiting for ARM to revoke tokens...")  # usually takes <5 minutes
    retry_delay = 10
    for i in range(600 // retry_delay):
        list(client.subscriptions.list())
        current_token = credential.get_token(ARM_SCOPE)
        if current_token.token != first_token.token:
            print("silently completed a claims challenge")
            return
        time.sleep(retry_delay)
        print("...%i seconds" % ((i + 1) * retry_delay))

    print("inconclusive test -- the first ARM token hasn't been revoked")


# az login
browser_credential = InteractiveBrowserCredential(
    tenant_id=TENANT_ID, disable_automatic_authentication=True, enable_persistent_cache=True
)
record = browser_credential.authenticate()

# az foo
credential = SharedTokenCacheCredential(authentication_record=record)

test_cae(credential)
