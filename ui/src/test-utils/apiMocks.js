import { USER_QUERY } from "../user";
import { SAMPLES_QUERY } from "../components/Samples";
import { INSTITUTIONS_QUERY } from "../components/Institutions";

export const mockUser = {
  email: "admin@juno.com",
  firstName: "Han",
  lastName: "Solo",
};

export const mockSamples = [
  {
    laneId: "31663_7#113",
    sampleId: "5903STDY8059170",
    publicName: "CUHK_GBS177WT_16",
    hostStatus: "SKIN_AND_SOFT_TISSUE_INFECTION",
    serotype: "IA",
    submittingInstitution: {
      name: "National Reference Laboratories",
      country: "Israel",
    },
  },
  {
    laneId: "32820_2#367",
    sampleId: "5903STDY8113194",
    publicName: "JN_IL_ST31578",
    hostStatus: "PNEUMONIA",
    serotype: "VI",
    submittingInstitution: {
      name: "The Chinese University of Hong Kong",
      country: "China",
    },
  },
];

export const mockInstitutions = [
  {
    name: "Wellcome Sanger Institute",
    country: "United Kingdom",
    latitude: 52.083333,
    longitude: 0.183333,
  },
  {
    name: "National Reference Laboratories",
    country: "Israel",
    latitude: 32.083333,
    longitude: 34.8,
  },
  {
    name: "The Chinese University of Hong Kong",
    country: "China",
    latitude: 22.419722,
    longitude: 114.206792,
  },
];

export const mockDefaults = {
  user: mockUser,
  samples: mockSamples,
  institutions: mockInstitutions,
};
export const generateApiMocks = (mocks = mockDefaults) => {
  const { user, samples, institutions } = mocks;

  // call counts for test assertions
  let called = {
    userQuery: 0,
    samplesQuery: 0,
    institutionsQuery: 0,
  };
  return {
    called,
    mocks: [
      {
        request: {
          query: USER_QUERY,
        },
        result: () => {
          called.userQuery += 1;
          return {
            data: {
              me: user,
            },
          };
        },
      },
      {
        request: {
          query: SAMPLES_QUERY,
        },
        result: () => {
          called.samplesQuery += 1;
          return {
            data: {
              samples,
            },
          };
        },
      },
      {
        request: {
          query: INSTITUTIONS_QUERY,
        },
        result: () => {
          called.institutionsQuery += 1;
          return {
            data: {
              institutions,
            },
          };
        },
      },
    ],
  };
};
