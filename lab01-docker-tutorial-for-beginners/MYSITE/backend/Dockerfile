# -------------------- BUILD STAGE --------------------
# only needed during the build process, not actually needed in production
# build process can generate many unwanted files like caches and logs
# security risk having build tools available on a production machine 
# Use a lightweight Python base image for building dependencies leaves a much greater attack surface
# that's why we separate the build process from the run process (multi-stage build)
FROM python:3.12-slim AS builder

# Set working directory inside the container
WORKDIR /app

# copy over our requirements txt 
# Copy dependency files first to leverage Docker caching
COPY pyproject.toml requirements.txt ./

# run pip install to install our requirements
# Install dependencies as pre-built wheels (precompiled packages - see them as zip files) into a local directory
RUN pip wheel --no-cache-dir --no-deps --wheel-dir wheels -r requirements.txt

# copy over rest of our source
# we copy source in a different copy command than the requirements 
# because if nothing changes Docker cash previous commands including this run requirements files change far less frequently
# a change in the source file and no change in the requirements will not require rerunning the pip install
COPY src src

# Optional: build any remaining wheels from the source code (if needed)
RUN pip wheel --no-cache-dir --no-deps --wheel-dir wheels .

# -------------------- RUN STAGE --------------------
# Use a fresh lightweight Python image for running the app
FROM python:3.12-slim AS runner

# Copy the prebuilt wheels from the builder stage
COPY --from=builder /app/wheels /wheels

# Install the wheels and clean up to reduce image size
# by adding 2 commands in a single run we decrease the number of layers
RUN pip install --no-cache /wheels/* && rm -rf /wheels

#basically just documentation for the reader since we still need to use docker run -p
EXPOSE 8000

# Default command to run the FastAPI app using Uvicorn
# This will be executed unless overridden by `docker run` arguments
# this command is used by adding /bin/sh
# list of strings approach
CMD ["uvicorn", "mysite.main:app", "--host", "0.0.0.0", "--port", "8000"]