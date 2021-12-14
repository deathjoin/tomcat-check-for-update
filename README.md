# tomcat-check-for-update

Python script to check for new tomcat versions compared to private docker registry image tags.

Script parses tomcat download webpage to find current latest version, then it runs few queries on specified registry to find out latest image version. It compares between to version and writes .env file that can be used in CI or manually to decide update in registry or not.

## Usage
```bash
./tomcat-checker.py --registryUrl="https://registry:5000" --registryImage="tomcat"
```

## Options
* `registryUrl` — url to docker registry where tomcat images contains.
* `registryImage` — name of the tomcat image repository in specified registry.
* `outputEnvFile`— name of the output .env file where values like `IMAGE_UPDATE_VERSION`, `IMAGE_NEED_UPDATE`, `IMAGE_DOWNLOAD_URL` will be stored.
* `forceUpdate` — get download link and set `IMAGE_NEED_UPDATE` to `True` anyway.