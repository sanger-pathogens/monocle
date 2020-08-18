import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile, login } from "../utils";

// Test button exists with data in database (admin user)
// Test button exists without data in database (admin user)
// Test no button when logged in as non admin
// Test drag over activates button (correct file)
// Test drag over with wrong file type shows error
// Test dropping file shows results, commit and cancel button
// Test commit changes the database

describe("upload button", () => {
  it("Drag drop exists when database is empty", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // empty samples table?
      expect(db.sample.length).to.equal(0);

      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // drag and drop does exist
      cy.get("#uploadButton").should(
        "contain",
        `Click here or drop a file to upload!`
      );
    });
  });

  it("drag drop exists when database contains samples", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // drag and drop does exists
      cy.get("#uploadButton").should(
        "contain",
        `Click here or drop a file to upload!`
      );
    });
  });

  it("uploads file from filesystem", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      cy.upload_file("#uploadButton", "test.xlsx");
    });
  });
});
