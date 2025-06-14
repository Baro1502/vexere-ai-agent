# Makefile
# Default environment
DEFAULT_ENVIRONMENT := dev

# Read the environment argument (if provided) or use the default
ifdef ENVIRONMENT
  TARGET_ENVIRONMENT := $(ENVIRONMENT)
else
  TARGET_ENVIRONMENT := $(DEFAULT_ENVIRONMENT)
endif

# Validate the environment argument
ifeq ($(filter $(TARGET_ENVIRONMENT),dev staging prod),)
  $(error Invalid environment "$(TARGET_ENVIRONMENT)". Use one of: dev, staging, prod)
endif

# Start the services in the specified environment
start:
	pm2 start pm2.config.json --env $(TARGET_ENVIRONMENT) || exit 1; \

# Stop the services
stop:
	pm2 stop $(SERVICE) || exit 1;

# Restart the services in the specified environment
restart:
	@echo "Restarting services in $(TARGET_ENVIRONMENT) environment..."
	$(MAKE) clean
	$(MAKE) start

# Kill all processes
kill:
	pm2 delete $(SERVICE) || exit 1

# Clean processes and logs
clean:
	pm2 flush
	$(MAKE) stop
	$(MAKE) kill
	pm2 flush