import React from "react";
import { useQuery } from "@apollo/react-hooks";
import gql from "graphql-tag";
import {
  Paper,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from "@material-ui/core";

const columns = [
  { key: "laneId", label: "Lane ID" },
  { key: "publicName", label: "Public Name" },
  { key: "submittingInstitutionName", label: "Submitting Institution" },
  { key: "country", label: "Country" },
];

const SAMPLES_QUERY = gql`
  {
    samples {
      id
      laneId
      sampleId
      publicName
      submittingInstitutionName
    }
  }
`;

const Samples = () => {
  const { loading, error, data } = useQuery(SAMPLES_QUERY);

  let rows = [];
  if (data && !(loading || error)) {
    // TODO: Handle loading/error cases
    rows = data.samples;
  }
  return (
    <TableContainer component={Paper}>
      <Table size="small" aria-label="a dense table">
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column.key}>{column.label}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row, i) => (
            <TableRow key={i}>
              {columns.map((column) => (
                <TableCell key={column.key}>{row[column.key]}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default Samples;
