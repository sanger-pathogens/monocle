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
import getLaneUrl from "./SampleDownload";
import DownloadButton from "./DownloadButton";

const columns = [
  { key: "laneId", label: "Lane ID", valueAccessor: (d) => d.laneId },
  {
    key: "publicName",
    label: "Public Name",
    valueAccessor: (d) => d.publicName,
  },
  {
    key: "submittingInstitution.name",
    label: "Submitting Institution",
    valueAccessor: (d) => d.submittingInstitution.name,
  },
  {
    key: "submittingInstitution.country",
    label: "Country",
    valueAccessor: (d) => d.submittingInstitution.country,
  },
  {
    key: "hostStatus",
    label: "Host Status",
    valueAccessor: (d) => d.hostStatus,
  },
  {
    key: "serotype",
    label: "Serotype",
    valueAccessor: (d) => d.serotype,
  },
  {
    key: "download",
    label: "Download",
    valueAccessor: (d) => (
      <DownloadButton
        url={getLaneUrl(d.laneId)}
        filename={d.laneId + ".tar.gz"}
      >
        {d.laneId}
      </DownloadButton>
    ),
  },
];

const SAMPLES_QUERY = gql`
  {
    samples {
      laneId
      sampleId
      publicName
      hostStatus
      serotype
      submittingInstitution {
        name
        country # TODO: replace submittingInstitution.country with samples.country
      }
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
      <Table size="small" aria-label="a dense table" id="sampleTable">
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
                <TableCell key={column.key} className={column.key}>
                  {column.valueAccessor(row)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default Samples;
