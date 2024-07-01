import boto3
    

def get_env():
    session = boto3.session.Session()
    client = session.client(
        service_name='ssm',
        region_name='ap-northeast-1'
    )

    response = client.get_parameters(
        Names=[
            '/Inventory-Risk-Manager/dev/api',
            '/Inventory-Risk-Manager/prod/api',
            '/HyperLiquid/prod/account-address',
            '/HyperLiquid/prod/neu-address'

        ],
        WithDecryption=True
    )

    return response['Parameters']