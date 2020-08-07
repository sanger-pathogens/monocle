import React, { useState } from "react";

export const DownloadingContext = React.createContext();

export const DownloadingProvider = (props) => {
  // exposed state
  const [isDownloading, setIsDownloading] = useState(false);

  return (
    <DownloadingContext.Provider
      value={{ isDownloading, setIsDownloading }}
      {...props}
    />
  );
};

export const useDownloading = () => React.useContext(DownloadingContext);
