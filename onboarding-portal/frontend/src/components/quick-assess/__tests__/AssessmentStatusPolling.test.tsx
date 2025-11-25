import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import apiClient from '@/services/api';
import { AssessmentStatusPolling } from '../AssessmentStatusPolling';

jest.mock('@/services/api', () => ({
  __esModule: true,
  default: {
    getAssessmentStatus: jest.fn(),
    getAssessmentResults: jest.fn(),
    shareAssessmentReport: jest.fn(),
  },
}));

const mockedApi = apiClient as jest.Mocked<typeof apiClient>;

describe('AssessmentStatusPolling', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockedApi.getAssessmentStatus.mockReset();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('polls status and updates progress stages', async () => {
    mockedApi.getAssessmentStatus.mockResolvedValue({
      assessment_id: 'qa-1',
      status: 'processing',
      stage: 'parsing',
      progress: 35,
      estimated_seconds_remaining: 120,
      files: [{ filename: 'doc1.docx', status: 'processing' }],
      error_messages: [],
    });

    render(<AssessmentStatusPolling assessmentId="qa-1" />);

    await waitFor(() =>
      expect(screen.getByText('Parsing documents...')).toBeInTheDocument()
    );

    expect(screen.getByText('doc1.docx')).toBeInTheDocument();
    act(() => {
      jest.advanceTimersByTime(5000);
    });
    expect(mockedApi.getAssessmentStatus).toHaveBeenCalledTimes(2);
  });

  it('shows error alert and retries polling', async () => {
    mockedApi.getAssessmentStatus
      .mockRejectedValueOnce(new Error('boom'))
      .mockResolvedValue({
        assessment_id: 'qa-2',
        status: 'processing',
        stage: 'ingestion',
        progress: 10,
        files: [],
        error_messages: [],
      });

    render(<AssessmentStatusPolling assessmentId="qa-2" />);

    await waitFor(() =>
      expect(screen.getByText('Status check failed')).toBeInTheDocument()
    );

    fireEvent.click(screen.getByRole('button', { name: /retry now/i }));

    await waitFor(() =>
      expect(mockedApi.getAssessmentStatus).toHaveBeenCalledTimes(2)
    );
  });
});

