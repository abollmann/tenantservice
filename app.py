from tenantservice import app
from tenantservice.consumer import ApartmentCommandConsumer

from config import APP_HOST

if __name__ == '__main__':
    ApartmentCommandConsumer().start()
    app.run(host=APP_HOST, port=5003)
