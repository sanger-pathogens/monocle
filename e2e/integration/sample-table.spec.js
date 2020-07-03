import { DB_PROFILES, loadDatabaseProfile, login, logout } from "../utils";

describe("sample table", () => {
  beforeEach(() => {
    // clean auth state
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it("exists", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // table exists?
      cy.get(`table#sampleTable`).should("exist");
    });
  });

  it("is empty when the database is empty", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // empty samples table?
      expect(db.sample.length).to.equal(0);

      // login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // table empty?
      cy.get(`table#sampleTable`).should("exist");
      cy.get(`table#sampleTable tbody tr`).should("not.exist");
    });
  });

  it("is populated when the database is non-empty as sanger user", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // table contains database entries?
      db.sample.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });

  it("is populated when the database is non-empty as collaborator", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // login as collaborating user (can view subset of samples only)
      cy.visit("/");
      const user = db.user[1];
      login(user.email);

      // calculate allowed
      const affiliations = db.affiliation.filter(
        (d) => d.user_id === user.email
      );
      const institutionsAllowed = affiliations.map((d) => d.institution_id);
      const samplesAllowed = db.sample.filter(
        (d) => institutionsAllowed.indexOf(d.submitting_institution_id) >= 0
      );
      const samplesDisallowed = db.sample.filter(
        (d) => institutionsAllowed.indexOf(d.submitting_institution_id) < 0
      );

      // some samples should be visible, some not?
      expect(samplesAllowed.length).to.be.greaterThan(0);
      expect(samplesDisallowed.length).to.be.greaterThan(0);

      // table contains allowed database entries?
      samplesAllowed.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });

      // table does not contain disallowed database entries?
      samplesDisallowed.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id).should("not.exist");
      });
    });
  });
});
