import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile, login } from "../utils";
import "cypress-file-upload";

// Test button exists with data in database (admin user) - DONE
// Test button exists without data in database (admin user) - DONE
// Test no button when logged in as non admin - DONE
// Test drag over activates button (correct file)
// Test drag over with wrong file type shows error
// Test dropping file shows results, commit and cancel button
// Test commit disabled when missing institution
// Test commit changes the database

describe("upload button", () => {
  // beforeEach(function () {
  //   this.dropEvent = {
  //     dataTransfer: {
  //       files: [
  //         { path: "/Users/km22/Documents/git_projects/monocle/e2e/mock_data" },
  //       ],
  //     },
  //   };
  // });

  it("shows update button above empty samples table as Sanger user", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // has button?
      cy.contains("Update metadata from spreadsheet").should("exist");
    });
  });

  it("shows update button above non-empty samples table as Sanger user", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // has button?
      cy.contains("Update metadata from spreadsheet").should("exist");
    });
  });

  it("does not show update button above samples table as non-Sanger user", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[1];
      login(user.email);

      // no button?
      cy.contains("Update metadata from spreadsheet").should("not.exist");
    });
  });

  // it("dropzone exists", () => {
  //   loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
  //     // empty samples table?
  //     expect(db.sample.length).to.equal(0);

  //     // load and login
  //     cy.visit("/");
  //     const user = db.user[0];
  //     login(user.email);

  //     //
  //     cy.get('button').contains('Update metadata from spreadsheet').click()
  //     cy.visit("/upload");

  //     // drag and drop does exist
  //     cy.get("#uploadButton").should(
  //       "contain",
  //       `Click here or drop a file to upload!`
  //     );
  //   });
  // });

  // it("drag drop exists when database contains samples", () => {
  //   loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
  //     // non-empty samples table?
  //     expect(db.sample.length).to.be.greaterThan(0);

  //     // load and login
  //     cy.visit("/");
  //     const user = db.user[0];
  //     login(user.email);

  //     // drag and drop does exists
  //     cy.get("#uploadButton").should(
  //       "contain",
  //       `Click here or drop a file to upload!`
  //     );
  //   });
  // });

  // it("drag and drop button is not there for non-sanger user", () => {
  //   loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
  //     cy.visit("/");

  //     // credentials
  //     const user = db.user[1];
  //     const { email, first_name, last_name } = user;

  //     // fill in credentials form and submit
  //     login(email);

  //     // drag and drop does not exist
  //     cy.get("body")
  //       .contains("Click here or drop a file to upload!")
  //       .should("not.exist");
  //   });
  // });

  // it.only("uploads file from filesystem", () => {
  //   loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
  //     // load and login
  //     cy.visit("/");
  //     const user = db.user[0];
  //     login(user.email);

  //     const yourFixturePath = "test.xlsx";
  //     cy.get("#uploadButton").attachFile(yourFixturePath);
  //   });
  // });
});
