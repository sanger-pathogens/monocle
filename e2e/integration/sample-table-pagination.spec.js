import { DB_PROFILES, API_WAIT_MS, loadDatabaseProfile, login } from "../utils";

describe("sample table pagination", () => {
  beforeEach(() => {
    // clean auth state
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it("shows first page only by default", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // table contains first page only?
      const firstPage = db.sample.slice(0, pageSize);
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      firstPage.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });

  it("shows second page on clicking next", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click next page button and await load
      cy.get('button[aria-label="next page"]').click();
      cy.wait(API_WAIT_MS);

      // table contains second page only?
      const secondPage = db.sample.slice(pageSize, pageSize * 2);
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      secondPage.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });

  it("shows first page again on clicking next then previous", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click next page button and await load
      cy.get('button[aria-label="next page"]').click();
      cy.wait(API_WAIT_MS);

      // click previous page button and await load
      cy.get('button[aria-label="previous page"]').click();
      cy.wait(API_WAIT_MS);

      // table contains first page only?
      const firstPage = db.sample.slice(0, pageSize);
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      firstPage.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });

  it("shows last page on clicking last", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click last page button and await load
      cy.get('button[aria-label="last page"]').click();
      cy.wait(API_WAIT_MS);

      // table contains second page only?
      const lastPageIndex = Math.floor(db.sample.length / pageSize);
      const lastPage = db.sample.slice(
        pageSize * lastPageIndex,
        db.sample.length
      );
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      lastPage.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });

  it("shows first page again on clicking last then first", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click last page button and await load
      cy.get('button[aria-label="last page"]').click();
      cy.wait(API_WAIT_MS);

      // click first page button and await load
      cy.get('button[aria-label="first page"]').click();
      cy.wait(API_WAIT_MS);

      // table contains first page only?
      const firstPage = db.sample.slice(0, pageSize);
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      firstPage.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });
});
