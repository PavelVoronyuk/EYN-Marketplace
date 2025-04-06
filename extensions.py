from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

mail = Mail()
limiter = Limiter(get_remote_address)