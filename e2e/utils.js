// it is possible that tests fail due to an slow API request,
// but we wait for the following amount of time, to hopefully
// mitigate this
export const API_WAIT_MS = 5000;

// object to make allowed database profiles more obvious
export const DB_PROFILES = {
  EMPTY: "empty",
  SMALL: "small",
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
