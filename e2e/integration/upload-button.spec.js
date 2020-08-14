import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile, login } from "../utils";

// let image = {
//   name: "cat.jpg",
//   size: 1000,
//   type: "image/jpeg",
// };

describe("upload button", () => {
  beforeEach(function () {
    this.dropEvent = {
      dataTransfer: {
        files: [
          { path: "/Users/km22/Documents/git_projects/monocle/e2e/mock_data" },
        ],
      },
    };
  });

  it("Drag drop exists when database is empty", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // empty samples table?
      expect(db.sample.length).to.equal(0);

      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // drag and drop does exist
      cy.get("body").should("contain", `Click here or drop a file to upload!`);
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
      cy.get("body").should("contain", `Click here or drop a file to upload!`);
    });
  });

  // it("drag drop activates when clicked", () => {
  //   loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
  //     // non-empty samples table?
  //     expect(db.sample.length).to.be.greaterThan(0);

  //     // load and login
  //     cy.visit("/");
  //     const user = db.user[0];
  //     login(user.email);

  //     //TODO: Check pop up file selector
  //     cy.get("body").contains(`Click here or drop a file to upload!`).click();
  //   });
  // });

  // it("drag drop activates when file dragged over", () => {
  //   loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
  //     // non-empty samples table?
  //     expect(db.sample.length).to.be.greaterThan(0);

  //     // load and login
  //     cy.visit("/");
  //     const user = db.user[0];
  //     login(user.email);

  //     // drag drop activates
  //     cy.get(Dropzone);
  //   });
  // });
});
