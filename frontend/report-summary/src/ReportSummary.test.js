const React = require("react");
const renderer = require("react-test-renderer");
const { ReportSummary } = require("./ReportSummary");

test("zeigt NO-GO und die Begründung", () => {
  const tree = renderer
    .create(
      React.createElement(ReportSummary, {
        report: {
          decision: "NO-GO",
          functional_decision: "NO-GO",
          weighted_pass_rate: "62.5 %",
          reasons: ["REQ-HIGH unerwartet fehlgeschlagen"],
        },
      }),
    )
    .toJSON();
  const blob = JSON.stringify(tree);
  expect(blob).toContain("NO-GO");
  expect(blob).toContain("REQ-HIGH unerwartet fehlgeschlagen");
  expect(tree.props["data-decision"]).toBe("NO-GO");
});

test("zeigt CONDITIONAL, wenn die Funktion steht und ein Restrisiko bleibt", () => {
  const tree = renderer
    .create(
      React.createElement(ReportSummary, {
        report: {
          decision: "CONDITIONAL",
          functional_decision: "GO",
          weighted_pass_rate: "91.0 %",
          reasons: ["DEF-SEC-01 offen"],
        },
      }),
    )
    .toJSON();
  const blob = JSON.stringify(tree);
  expect(blob).toContain("CONDITIONAL");
  expect(blob).toContain("Funktional: GO");
  expect(blob).toContain("DEF-SEC-01 offen");
});
