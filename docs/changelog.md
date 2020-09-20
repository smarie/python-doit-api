# Changelog

### 0.6.1 - New `doit_config` + API change to support multiprocessing

 * New `doit_config()` utility method to generate a valid `DOIT_CONFIG` in its caller module. Fixes [#1](https://github.com/smarie/python-doit-api/issues/1)

 * The `task` API was not compliant with the `num_process` option in the configuration, enabling multiprocess execution of doit. In order to fix the issue (an issue with pickle), `task` was split into two: `@pytask` is the decorator, and `task` is the creator. Fixed [#3](https://github.com/smarie/python-doit-api/issues/3) 

### 0.5.0 - First public version

 * Initial release with `task`, `taskgen`, `title_with_actions` and `why_am_i_running`.
