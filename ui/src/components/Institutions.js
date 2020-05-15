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
  { key: "name", label: "Institution" },
  { key: "country", label: "Country" },
];

const INSTITUTIONS_QUERY = gql`
  {
    institutions {
      name
      country
    }
  }
`;

const Institutions = () => {
  const { loading, error, data } = useQuery(INSTITUTIONS_QUERY);

  let rows = [];
  if (data && !(loading || error)) {
    // TODO: Handle loading/error cases
    rows = data.institutions;
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

export default Institutions;
