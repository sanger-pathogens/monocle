export async function loadUserRole(fetch) {
  const userRole = await fetch("http://monocle.dev.pam.sanger.ac.uk/dashboard-api/get_user_details")
    .then((response) =>
      response.ok ? response.json() : Promise.reject(`${response.status} ${response.statusText}`))
    .then(({ user_details }) => user_details?.type)
    .catch((err) => (
      console.log(`Error while fetching user details: ${err}`)
    ));
  return userRole;
}
