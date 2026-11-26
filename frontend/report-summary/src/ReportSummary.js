/**
 * Kleines React-Beispiel für die Stellenanzeige (React + Jest).
 * Es rendert nur Daten, die das Python-Reporting schon entschieden hat.
 * Es ist nicht die veryops-Website und spricht kein Netzwerk an.
 */
const React = require("react");

function ReportSummary({ report }) {
  const reasons = report.reasons || [];
  return React.createElement(
    "section",
    { "aria-label": "Release-Readiness", "data-decision": report.decision },
    React.createElement("h2", null, report.decision),
    React.createElement("p", null, "Funktional: " + report.functional_decision),
    React.createElement("p", null, "Gewichtete Pass-Rate: " + report.weighted_pass_rate),
    React.createElement(
      "ul",
      null,
      reasons.map((reason) => React.createElement("li", { key: reason }, reason)),
    ),
  );
}

module.exports = { ReportSummary };
