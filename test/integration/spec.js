it("detects angry sentiment", () => {
  cy.visit("/");

  // TODO: refine
  cy.get("body").should("contain", "National Reference Laboratories");
});
