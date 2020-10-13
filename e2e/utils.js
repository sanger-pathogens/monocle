// it is possible that tests fail due to an slow API request,
// but we wait for the following amount of time, to hopefully
// mitigate this
export const API_WAIT_MS = 5000;

// object to make allowed database profiles more obvious
export const DB_PROFILES = {
  EMPTY: "empty",
  SMALL: "small",
  LARGE: "large",
};

// use custom django management command `e2e` to change
// database content via python and return database content
// to test in javascript via stdout
export const loadDatabaseProfile = (profileName) =>
  cy
    .exec(`./run-on-api.sh python manage.py e2e ${profileName}`)
    .then(({ code, stdout, stderr }) => {
      // check db update ok
      let data;
      if (code === 0) {
        data = JSON.parse(stdout);
      } else {
        cy.task("log", stderr);
      }

      // return database data for test
      return data;
    });

// authentication utils
export const login = (email) => {
  // password is email prefix (for tests only)
  const password = email.split("@")[0];

  // fill in credentials
  cy.get("input[type=email]").type(email);
  cy.get("input[type=password]").type(password);
  cy.get("button[type=submit]").click();

  // await page change
  cy.wait(API_WAIT_MS);
};
export const logout = () => {
  // click the profile menu
  cy.get("#buttonProfileMenu").click();

  // now click logout button
  cy.contains("Logout").click();

  // await page change
  cy.wait(API_WAIT_MS);
};
