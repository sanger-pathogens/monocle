import { DB_PROFILES, API_WAIT_MS, loadDatabaseProfile, login } from "../utils";

describe("sample table sorting", () => {
  beforeEach(() => {
    // clean auth state
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  const fieldComparator = (accessor, ascending = true) => (a, b) => {
    const vA = accessor(a);
    const vB = accessor(b);
    const multiplier = ascending ? 1 : -1;
    if (vA < vB) {
      return -1 * multiplier;
    } else if (vA > vB) {
      return multiplier;
    } else {
      return 0;
    }
  };

  it("defaults to sorting by sampleId ascending", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // table contains first page sorted by sampleId ascending only?
      const firstPage = db.sample
        .sort(fieldComparator((d) => d.sample_id, true))
        .slice(0, pageSize);
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      firstPage.forEach(({ sample_id }) => {
        cy.get(`table#sampleTable`).contains("td", sample_id);
      });
    });
  });

  it("changes to sorting by sampleId descending on clicking the sampleId column header", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click the sampleId column header
      cy.contains("Sample ID").click();

      // table contains first page sorted by sampleId descending only?
      const firstPage = db.sample
        .sort(fieldComparator((d) => d.sample_id, false))
        .slice(0, pageSize);
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      firstPage.forEach(({ sample_id }) => {
        cy.get(`table#sampleTable`).contains("td", sample_id);
      });
    });
  });

  it("changes to sorting by laneId ascending on clicking the laneId column header", () => {
    loadDatabaseProfile(DB_PROFILES.LARGE).then((db) => {
      const pageSize = 10;

      // non-empty samples table with more than one page?
      expect(db.sample.length).to.be.greaterThan(pageSize);

      // login as sanger user (can view all samples)
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click the laneId column header
      cy.contains("Lane ID").click();

      // table contains first page sorted by laneId ascending only?
      const firstPage = db.sample
        .sort(fieldComparator((d) => d.lane_id, true))
        .slice(0, pageSize);
      cy.get("table#sampleTable tbody")
        .find("tr")
        .should("have.length", pageSize);
      firstPage.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });
});
