import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile, login } from "../utils";

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

  it("is populated when the database is non-empty", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // table contains database entries?
      db.sample.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });
});
