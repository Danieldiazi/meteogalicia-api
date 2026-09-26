These JSON snapshots were retrieved from the public MeteoGalicia service on
2026-09-26 for municipality 15030 (A Coruña), using `dia=-1` and `dia=1`:

- https://servizos.meteogalicia.gal/mgrss/predicion/adversos/jsonAvisosConcellos.action
- https://servizos.meteogalicia.gal/mgrss/predicion/adversos/jsonConcellosNivelMax.action

Only JSON whitespace was changed. All requests returned HTTP 200. Empty warning
lists and level zero represent a valid forecast without warnings, not a failure.
