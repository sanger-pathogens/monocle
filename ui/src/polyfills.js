// polyfills for variable browser support of new web features

import "web-streams-polyfill/dist/polyfill";
import { TextEncoder, TextDecoder } from "text-encoding-polyfill";
window.TextEncoder = TextEncoder;
window.TextDecoder = TextDecoder;
