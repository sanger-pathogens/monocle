export const DATA_TYPE_METADATA = "metadata";

export const DATA_TYPE_IN_SILICO = "in silico";

export const DATA_TYPE_QC = "qc data";

export const DATA_TYPES = [
  DATA_TYPE_METADATA,
  DATA_TYPE_IN_SILICO,
  DATA_TYPE_QC,
];

export const EMAIL_MONOCLE_HELP = "monocle-help@sanger.ac.uk";

export const HTTP_HEADER_CONTENT_TYPE = "Content-Type";

export const HTTP_HEADERS_JSON = { "Content-Type": "application/json" };

export const HTTP_POST = "POST";

export const HTTP_STATUS_CODE_UNAUTHORIZED = 401;

// IMPORTANT: when incrementing this key, put the old one to `SESSION_STORAGE_KEYS_OLD_COLUMNS_STATE`. This is
// needed to clear `sessionStorage` from old data (otherwise it's cleared only on closing the browser tab/window).
export const SESSION_STORAGE_KEY_COLUMNS_STATE = "columnsState_7";
export const SESSION_STORAGE_KEYS_OLD_COLUMNS_STATE = [
  "columnsState",
  "columnsState_1",
  "columnsState_2",
  "columnsState_3",
  "columnsState_4",
  "columnsState_5",
  "columnsState_6",
];

export const MIME_TYPE_HTML = "text/html";

export const PATHNAME_LOGIN = "/login";

export const USER_ROLE_ADMIN = "admin";
