import env from "./env";

const REFRESH_TOKEN_MUTATION = `
  mutation RefreshToken {
    refreshToken {
      payload
      token
      refreshExpiresIn
    }
  }
`;

const refreshToken = () =>
  fetch(env.GRAPHQL_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ query: REFRESH_TOKEN_MUTATION }),
  });

export default refreshToken;
