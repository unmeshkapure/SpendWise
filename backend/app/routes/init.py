from . import auth
from . import transactions
from . import dashboard
from . import predictions
from . import goals
from . import badges

# Make sure all modules are accessible as attributes
from .auth import router as auth_router
from .transactions import router as transactions_router
from .dashboard import router as dashboard_router
from .predictions import router as predictions_router
from .goals import router as goals_router
from .badges import router as badges_router

# Assign them to the module so they can be accessed as attributes
import sys
import importlib

# Get the current module
current_module = sys.modules[__name__]

# Import and assign each route module
current_module.auth = importlib.import_module('app.routes.auth')
current_module.transactions = importlib.import_module('app.routes.transactions')
current_module.dashboard = importlib.import_module('app.routes.dashboard')
current_module.predictions = importlib.import_module('app.routes.predictions')
current_module.goals = importlib.import_module('app.routes.goals')
current_module.badges = importlib.import_module('app.routes.badges')