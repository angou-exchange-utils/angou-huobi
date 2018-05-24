angou\_huobi 2 (May 24, 2018)
===
- `angou_huobi.rest` now exposes a module-scoped `LOGGER` variable, instead of
  per-class `angou_huobi.rest.RestSession.logger`s.
- If a response has a “success” HTTP status code but its body cannot be parsed
  as JSON, `angou_huobi.rest.InvalidJSON` is raised.
- `angou_huobi.rest.RestSession` constructor now takes an optional `timeout`
  argument.

angou\_huobi 1 (May 19, 2018)
===
The first release of angou\_huobi!
