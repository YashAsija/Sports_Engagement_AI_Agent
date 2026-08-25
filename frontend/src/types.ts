export interface GroundingSource {
  source_type: 'web_search' | 'chromadb' | 'opinion_based' | 'fallback_verified';
  citation_title: string;
  url_or_id?: string;
  display_source?: string;
  snippet?: string;
}

export type ContentFormatType = 
  | 'MCQ' 
  | 'True / False' 
  | 'This-or-That Poll' 
  | 'Fill in the Blank' 
  | 'Guess the Number';

export interface ContentItem {
  id: string;
  format: ContentFormatType;
  sport: string;
  difficulty?: string;
  question?: string;
  statement?: string;
  prompt?: string;
  sentence_with_blank?: string;
  options?: string[];
  correct_answer?: string;
  target_number?: number;
  accepted_tolerance_range?: string;
  is_opinion?: boolean;
  explanation: string;
  grounding: GroundingSource;
}

export type RetrievalSourceOption = 'web_search' | 'chromadb' | 'both';

export interface BatchGenerationParams {
  sport: string;
  difficulty: string;
  content_format: string;
  count: number;
  retrieval_source: RetrievalSourceOption;
}
