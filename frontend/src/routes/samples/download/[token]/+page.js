// Extract `token` from the URL path and pass it to the page component as a prop.
export function load({ params }) {
  return { downloadToken: params.token };
}
