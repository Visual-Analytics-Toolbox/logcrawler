# Logcrawler
The logcrawler is intended for inserting data from the logs to a postgres database. It expects that it has access to a visual analytics tool instance and a labelstudio instance and filesystem access to the logs.

## Development
You will need these environment variables in order to run the scripts:
```bash
VAT_LOG_ROOT=<"path to folder containing all the log data">
VAT_API_URL=<"http://127.0.0.1:8000/">
VAT_API_TOKEN=<api token for the visual analytics instance>
LABELSTUDIO_API_KEY=<api token for the labelstudio instance>
```

For development we recommend using an .envrc file which enables you to quickly change those values.


### The C part
The extract_images.py script needs to verify how many images are in the extracted folder. ls is really slow if you have a couple thousand files in one folder. We wrote our own ls implementation that is much faster. The difference is most noteable if you access the log folder over network.

You can build the fast_ls binary with
```bash
gcc scripts/fast_ls.c -o fast_ls
```
