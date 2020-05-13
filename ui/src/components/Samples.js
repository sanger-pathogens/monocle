import React from "react";
import {
  Paper,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from "@material-ui/core";

import { samples } from "../mocks";

const columns = [
  { key: "laneId", label: "Lane ID" },
  { key: "publicName", label: "Public Name" },
  { key: "submittingInstitution", label: "Submitting Institution" },
  { key: "country", label: "Country" },
];

const Samples = () => (
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
        {samples.map((row, i) => (
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

export default Samples;
