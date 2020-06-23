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

it("loads the institutions table", () => {
  cy.visit("/");

  // body should contain data from the `institutions.json` fixture
  cy.get("body").should("contain", "National Reference Laboratories");
});

it("loads the samples table", () => {
  cy.visit("/");

  // body should contain data from the `samples.json` fixture
  cy.get("body").should("contain", "31663_7#113");
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
  cy.get("body").should("not.contain", "31663_7#113");
});
