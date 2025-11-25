import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import apiClient from '@/services/api';
import { AssessmentResults } from '../AssessmentResults';

jest.mock('@/services/api', () => ({
  __esModule: true,
  default: {
    getAssessmentStatus: jest.fn(),
    getAssessmentResults: jest.fn(),
    shareAssessmentReport: jest.fn(),
  },
}));

const mockedApi = apiClient as jest.Mocked<typeof apiClient>;

const sampleResults = {
  cloud_readiness_score: 82,
  key_findings: ['Modern containerized workloads', 'Needs DB HA'],
  infrastructure_counts: { servers: 4, databases: 2 },
  technology_stack: {
    languages: ['Python'],
    frameworks: ['FastAPI'],
    cloud_services: ['AWS'],
    databases: ['PostgreSQL'],
    storage: ['S3'],
  },
  risk_level: 'medium',
  report_url: 'https://example.com/report.pdf',
  report_json_url: 'https://example.com/report.json',
};

describe('AssessmentResults', () => {
  beforeEach(() => {
    window.open = jest.fn();
    mockedApi.shareAssessmentReport.mockReset();
  });

  it('renders readiness score and findings', () => {
    render(
      <AssessmentResults assessmentId="qa-3" initialData={sampleResults} />
    );

    expect(screen.getByText('Cloud Readiness Score')).toBeInTheDocument();
    expect(screen.getByText('82')).toBeInTheDocument();
    expect(
      screen.getByText('Modern containerized workloads')
    ).toBeInTheDocument();
  });

  it('handles share action', async () => {
    Object.assign(navigator, {
      clipboard: { writeText: jest.fn() },
    });
    mockedApi.shareAssessmentReport.mockResolvedValue({
      share_url: 'https://share/link',
    });

    render(
      <AssessmentResults assessmentId="qa-4" initialData={sampleResults} />
    );

    fireEvent.click(screen.getByRole('button', { name: /share report/i }));
    await waitFor(() =>
      expect(mockedApi.shareAssessmentReport).toHaveBeenCalled()
    );
    expect(screen.getByText(/share link copied/i)).toBeInTheDocument();
  });
});

