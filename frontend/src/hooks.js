export async function getSession() {
	const user_role = await fetch("/get_user_details")
		.then((response) => response.json())
		.then(({ user_details: { type } }) => type)
		.catch((err) => (
			console.log(`Error while fetching user details: ${err}`)
		));

	return {
		user: {
			role: user_role
		}
	};
}
