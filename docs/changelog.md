# Changelog

### 0.8.0 - Multiline command actions

 * Multiline string command actions are now interpreted as to be concatenated into the same shell command using `&` (windows) or `;` (linux). This allows several commands to leverage each other, for example `conda activate` + some python execution. Fixes [#6](https://github.com/smarie/python-doit-api/issues/6)

### 0.7.0 - New `@cmdtask`

 * New `@cmdtask` similar to `@pytask` but to create shell commands. Fixes [#5](https://github.com/smarie/python-doit-api/issues/5)

### 0.6.1 - New `doit_config` + API change to support multiprocessing

 * New `doit_config()` utility method to generate a valid `DOIT_CONFIG` in its caller module. Fixes [#1](https://github.com/smarie/python-doit-api/issues/1)

 * The `task` API was not compliant with the `num_process` option in the configuration, enabling multiprocess execution of doit. In order to fix the issue (an issue with pickle), `task` was split into two: `@pytask` is the decorator, and `task` is the creator. Fixed [#3](https://github.com/smarie/python-doit-api/issues/3) 

### 0.5.0 - First public version

 * Initial release with `task`, `taskgen`, `title_with_actions` and `why_am_i_running`.
