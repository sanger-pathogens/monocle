import React from "react";
import {
  Paper,
  Box,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableFooter,
  TableRow,
  TableCell,
  IconButton,
  Typography,
} from "@material-ui/core";
import {
  FirstPage,
  KeyboardArrowLeft,
  KeyboardArrowRight,
  LastPage,
} from "@material-ui/icons";
import { useTable, usePagination } from "react-table";

// see https://github.com/tannerlinsley/react-table/discussions/2296

const DataTable = ({
  tableId,
  columns,
  data,
  totalCount,
  fetchData,
  loading,
  pageCount: controlledPageCount,
  pageSize: controlledPageSize,
}) => {
  const {
    rows,
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    canPreviousPage,
    canNextPage,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data,
      initialState: { pageIndex: 0, pageSize: controlledPageSize },
      manualPagination: true,
      pageCount: controlledPageCount,
    },
    usePagination
  );

  React.useEffect(() => {
    fetchData({ pageIndex, pageSize });
  }, [fetchData, pageIndex, pageSize]);

  return (
    <Paper>
      <TableContainer>
        <Table {...getTableProps()} id={tableId} size="small">
          <TableHead>
            {headerGroups.map((headerGroup) => (
              <TableRow {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map((column) => (
                  <TableCell {...column.getHeaderProps()}>
                    {column.render("Header")}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody {...getTableBodyProps()}>
            {rows.map((row, i) => {
              prepareRow(row);
              return (
                <TableRow {...row.getRowProps()}>
                  {row.cells.map((cell) => {
                    return (
                      <TableCell {...cell.getCellProps()}>
                        {cell.render("Cell")}
                      </TableCell>
                    );
                  })}
                </TableRow>
              );
            })}
          </TableBody>
          <TableFooter>
            <TableRow></TableRow>
          </TableFooter>
        </Table>
      </TableContainer>
      <Box textAlign="right" flexShrink={0} p={1}>
        <Box display="inline" pr={2}>
          <Typography variant="caption">
            {pageIndex * pageSize + 1}-{pageIndex * pageSize + rows.length} of{" "}
            {totalCount}
          </Typography>
        </Box>
        <IconButton
          onClick={() => gotoPage(0)}
          disabled={!canPreviousPage}
          aria-label="first page"
          size="small"
        >
          <FirstPage />
        </IconButton>
        <IconButton
          onClick={previousPage}
          disabled={!canPreviousPage}
          aria-label="previous page"
          size="small"
        >
          <KeyboardArrowLeft />
        </IconButton>
        <IconButton
          onClick={nextPage}
          disabled={!canNextPage}
          aria-label="next page"
          size="small"
        >
          <KeyboardArrowRight />
        </IconButton>
        <IconButton
          onClick={() => gotoPage(pageCount - 1)}
          disabled={!canNextPage}
          aria-label="last page"
          size="small"
        >
          <LastPage />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default DataTable;
