// it is possible that tests fail due to an slow API request,
// but we wait for the following amount of time, to hopefully
// mitigate this
const API_WAIT_MS = 1000;

it("loads the page", () => {
  cy.visit("/");

  // title is hard-coded in index.html (no dependence on react)
  cy.title().should("eq", "Monocle");
});

it("loads the react app", () => {
  cy.visit("/");

  // body should contain two tables, titled `Institutions` and `Samples`
  cy.get("body").should("contain", "Institutions");
  cy.get("body").should("contain", "Samples");
});

it("is possible to connect to api", () => {
  // run remote command via script
  // (eventually for db seeding)
  cy.exec("./run-on-api.sh ls -l /app");

  cy.visit("/");

  // title is hard-coded in index.html (no dependence on react)
  cy.title().should("eq", "Monocle");
});

it("is possible clear the database", () => {
  // run remote command via script
  // (eventually for db seeding)
  cy.exec("./run-on-api.sh python manage.py e2e empty");

  cy.visit("/");

  // title is hard-coded in index.html (no dependence on react)
  cy.title().should("eq", "Monocle");

  // body should NOT contain data from the `samples.json` fixture
  // cy.get("body").should("not.contain", "31663_7#113");
  cy.get("body").contains("31663_7#113").should("not.exist");
});

it("is possible retrieve seeded data from the database", () => {
  cy.exec("./run-on-api.sh python manage.py e2e small").then(
    ({ code, stdout, stderr }) => {
      // check db update ok
      let data;
      if (code === 0) {
        data = JSON.parse(stdout);
      } else {
        cy.task("log", stderr);
      }

      // test
      if (data) {
        cy.visit("/");
        cy.wait(API_WAIT_MS);
        data.sample.forEach(({ lane_id }) => {
          cy.get("body").contains(lane_id).should("exist");
        });
      }
    }
  );
});
