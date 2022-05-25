export const DATA_TYPE_METADATA = "metadata";

export const DATA_TYPE_IN_SILICO = "in silico";

export const DATA_TYPES = [DATA_TYPE_METADATA, DATA_TYPE_IN_SILICO];

export const EMAIL_MONOCLE_HELP = "monocle-help@sanger.ac.uk";

// IMPORTANT: when incrementing this key, put the old one to `LOCAL_STORAGE_KEYS_OLD_COLUMNS_STATE`. This is
// needed to clear `localStorage` from old data.
export const LOCAL_STORAGE_KEY_COLUMNS_STATE = "columnsState_2";
export const LOCAL_STORAGE_KEYS_OLD_COLUMNS_STATE = [
  "columnsState",
  "columnsState_1",
];

export const USER_ROLE_ADMIN = "admin";
