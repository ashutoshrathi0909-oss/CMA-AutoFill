// ============================================================================
// API Types — Matches backend FastAPI response shapes exactly
// ============================================================================

/** Standard API response wrapper from backend */
export interface ApiResponse<T> {
    data: T;
    error: null;
}

/** Standard API error response */
export interface ApiErrorResponse {
    data: null;
    error: {
        message: string;
        code?: string;
        details?: Record<string, unknown>;
    };
}

// ============================================================================
// Auth & User Types
// ============================================================================

export interface UserProfile {
    id: string;
    email: string;
    full_name: string;
    role: 'admin' | 'ca' | 'staff';
    firm_id: string;
    firm_name: string;
    avatar_url?: string;
    created_at: string;
    updated_at: string;
}

// ============================================================================
// Client Types
// ============================================================================

export type EntityType = 'partnership' | 'proprietorship' | 'company' | 'llp' | 'trading';

export interface Client {
    id: string;
    firm_id: string;
    name: string;
    entity_type: EntityType;
    pan?: string;
    gst?: string;
    contact_person?: string;
    email?: string;
    phone?: string;
    address?: string;
    projects_count?: number;
    created_at: string;
    updated_at: string;
    is_deleted?: boolean;
}

export interface ClientCreate {
    name: string;
    entity_type: EntityType;
    pan?: string;
    gst?: string;
    contact_person?: string;
    email?: string;
    phone?: string;
    address?: string;
}

export interface ClientUpdate extends Partial<ClientCreate> { }

export interface ClientListParams {
    search?: string;
    entity_type?: EntityType;
    page?: number;
    per_page?: number;
}

export interface ClientListResponse {
    clients: Client[];
    total: number;
    page: number;
    per_page: number;
}

// ============================================================================
// Project Types
// ============================================================================

export type ProjectStatus =
    | 'draft'
    | 'extracting'
    | 'classifying'
    | 'validating'
    | 'reviewing'
    | 'generating'
    | 'completed'
    | 'error';

export interface Project {
    id: string;
    firm_id: string;
    client_id: string;
    client_name?: string;
    financial_year: string;
    bank_name?: string;
    loan_type?: string;
    loan_amount?: number;
    status: ProjectStatus;
    pipeline_progress: number;
    error_message?: string;
    current_step?: string;
    created_at: string;
    updated_at: string;
    is_deleted?: boolean;
}

export interface ProjectCreate {
    client_id: string;
    financial_year: string;
    bank_name?: string;
    loan_type?: string;
    loan_amount?: number;
}

export interface ProjectUpdate extends Partial<ProjectCreate> {
    status?: ProjectStatus;
}

export interface ProjectListParams {
    search?: string;
    status?: ProjectStatus;
    client_id?: string;
    page?: number;
    per_page?: number;
}

export interface ProjectListResponse {
    projects: Project[];
    total: number;
    page: number;
    per_page: number;
}

// ============================================================================
// Pipeline Types
// ============================================================================

export interface PipelineStep {
    name: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
    started_at?: string;
    completed_at?: string;
    error?: string;
}

export interface PipelineProgress {
    project_id: string;
    status: ProjectStatus;
    pipeline_progress: number;
    current_step?: string;
    steps: PipelineStep[];
    error_message?: string;
}

// ============================================================================
// File Types
// ============================================================================

export interface UploadedFile {
    id: string;
    project_id: string;
    filename: string;
    file_type: string;
    file_size: number;
    storage_path: string;
    created_at: string;
}

export interface GeneratedFile {
    id: string;
    project_id: string;
    filename: string;
    file_type: string;
    storage_path: string;
    created_at: string;
}

// ============================================================================
// Review Queue Types
// ============================================================================

export type ReviewStatus = 'pending' | 'resolved' | 'auto_approved';

export interface ReviewItem {
    id: string;
    project_id: string;
    firm_id: string;
    source_item_name: string;
    suggested_category: string;
    suggested_subcategory?: string;
    confidence: number;
    classification_source: 'precedent' | 'rule' | 'ai';
    status: ReviewStatus;
    resolved_category?: string;
    resolved_subcategory?: string;
    resolved_by?: string;
    resolved_at?: string;
    created_at: string;
}

export interface ReviewResolvePayload {
    resolved_category: string;
    resolved_subcategory?: string;
}

export interface BulkResolvePayload {
    review_ids: string[];
    resolved_category: string;
    resolved_subcategory?: string;
}

export interface ReviewListParams {
    project_id?: string;
    status?: ReviewStatus;
    page?: number;
    per_page?: number;
}

export interface ReviewListResponse {
    items: ReviewItem[];
    total: number;
    page: number;
    per_page: number;
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardStats {
    total_clients: number;
    active_projects: number;
    pending_reviews: number;
    completed_this_month: number;
    total_cost_this_month?: number;
    projects_by_status: Record<ProjectStatus, number>;
    recent_projects: Project[];
}

// ============================================================================
// Precedent Types
// ============================================================================

export interface Precedent {
    id: string;
    firm_id: string;
    item_name: string;
    category: string;
    subcategory?: string;
    usage_count: number;
    created_at: string;
    updated_at: string;
}

export interface PrecedentCreate {
    item_name: string;
    category: string;
    subcategory?: string;
}

// ============================================================================
// Learning Metrics Types
// ============================================================================

export interface LearningMetrics {
    total_classifications: number;
    precedent_hit_rate: number;
    rule_hit_rate: number;
    ai_hit_rate: number;
    review_rate: number;
    auto_approve_rate: number;
    avg_confidence: number;
}

// ============================================================================
// Extraction & Classification Types
// ============================================================================

export interface ExtractionResult {
    project_id: string;
    extracted_items: ExtractedItem[];
    total_items: number;
}

export interface ExtractedItem {
    name: string;
    values: Record<string, number | string>;
    source_file?: string;
    page_number?: number;
}

export interface ClassificationResult {
    project_id: string;
    classified_items: number;
    review_items: number;
    auto_approved_items: number;
}

// ============================================================================
// Validation & Generation Types
// ============================================================================

export interface ValidationResult {
    is_valid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
}

export interface ValidationError {
    field: string;
    message: string;
    severity: 'error';
}

export interface ValidationWarning {
    field: string;
    message: string;
    severity: 'warning';
}

export interface GenerationResult {
    project_id: string;
    file_id: string;
    filename: string;
    download_url: string;
}

// ============================================================================
// Download & Validation Summary Types
// ============================================================================

export interface DownloadInfo {
    filename: string;
    file_size: number;
    generated_at: string;
    version: number;
}

export interface ValidationSummary {
    total_items: number;
    auto_classified: number;
    reviewed_by_ca: number;
}

// CMA Categories for Review UI
export const CMA_CATEGORIES = [
    // Income
    { group: 'Income', row: 1, label: 'Net Sales / Revenue from Operations' },
    { group: 'Income', row: 2, label: 'Other Income' },
    // Expenses
    { group: 'Expenses', row: 10, label: 'Raw Material Consumed' },
    { group: 'Expenses', row: 11, label: 'Purchase of Stock-in-Trade' },
    { group: 'Expenses', row: 12, label: 'Change in Inventories' },
    { group: 'Expenses', row: 13, label: 'Employee Benefits Expense' },
    { group: 'Expenses', row: 14, label: 'Finance Costs' },
    { group: 'Expenses', row: 15, label: 'Depreciation & Amortisation' },
    { group: 'Expenses', row: 16, label: 'Manufacturing Expenses' },
    { group: 'Expenses', row: 17, label: 'Administrative Expenses' },
    { group: 'Expenses', row: 18, label: 'Selling & Distribution Expenses' },
    { group: 'Expenses', row: 19, label: 'Other Operating Expenses' },
    // Assets
    { group: 'Assets', row: 30, label: 'Fixed Assets / Tangible Assets' },
    { group: 'Assets', row: 31, label: 'Capital WIP' },
    { group: 'Assets', row: 32, label: 'Investments' },
    { group: 'Assets', row: 33, label: 'Trade Receivables' },
    { group: 'Assets', row: 34, label: 'Cash & Cash Equivalents' },
    { group: 'Assets', row: 35, label: 'Short-term Loans & Advances' },
    { group: 'Assets', row: 36, label: 'Inventories / Stock' },
    { group: 'Assets', row: 37, label: 'Other Current Assets' },
    // Liabilities
    { group: 'Liabilities', row: 50, label: 'Share Capital' },
    { group: 'Liabilities', row: 51, label: 'Reserves & Surplus' },
    { group: 'Liabilities', row: 52, label: 'Long-term Borrowings' },
    { group: 'Liabilities', row: 53, label: 'Deferred Tax Liabilities' },
    { group: 'Liabilities', row: 54, label: 'Short-term Borrowings' },
    { group: 'Liabilities', row: 55, label: 'Trade Payables / Creditors' },
    { group: 'Liabilities', row: 56, label: 'Other Current Liabilities' },
    { group: 'Liabilities', row: 57, label: 'Provisions' },
    // Other
    { group: 'Other', row: 70, label: 'Miscellaneous / Not Applicable' },
    { group: 'Other', row: 71, label: 'Contingent Liabilities' },
] as const;
