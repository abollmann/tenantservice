from tenantservice import app
from tenantservice.consumer import TenantsConsumer

from config import APP_HOST

if __name__ == '__main__':
    TenantsConsumer().start()
    app.run(host=APP_HOST, port=5003)
