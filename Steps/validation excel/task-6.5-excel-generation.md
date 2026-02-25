# Task 6.5: Excel Generation Pipeline

> **Phase:** 06 - Validation & Excel Generation
> **Depends on:** Tasks 6.2 (validator), 6.3 (writer), 6.4 (transformer)
> **Agent reads:** CLAUDE.md → Reference Files
> **Time estimate:** 15 minutes

---

## Objective

Wire together validation → transformation → writing into a single generation pipeline. One function call takes a project and produces the CMA Excel file.

---

## What to Do

### Create File
`backend/app/services/excel/generator.py`

### Main Function

`generate_cma(project_id: UUID, firm_id: UUID, skip_validation: bool = False) → GenerationResult`

### Pipeline Steps

```
1. Load classification data from project
2. Run validation (unless skip_validation=True)
   → If errors → STOP, return validation errors
   → If only warnings → continue with warnings
3. Transform classified data → writer format
4. Copy CMA template to temp location
5. Write data into template
6. Save output file
7. Upload to Supabase Storage
8. Create record in generated_files table
9. Update project status → 'completed'
10. Return result
```

### Generation Result

```python
class GenerationResult:
    success: bool
    project_id: UUID
    generated_file_id: UUID | None
    file_name: str               # "CMA_MehtaComputers_2024-25_v1.xlsx"
    file_size: int
    storage_path: str
    validation: ValidationResult
    warnings: list[str]
    generation_time_ms: int
    version: int                 # auto-incremented per project
```

### File Naming Convention

`CMA_{ClientName}_{FinancialYear}_v{version}.xlsx`

Examples:
- `CMA_MehtaComputers_2024-25_v1.xlsx`
- `CMA_MehtaComputers_2024-25_v2.xlsx` (after corrections)

### Version Management

- Each generation creates a new version
- Query `generated_files` for this project → count + 1 = new version
- Keep all versions (never delete old ones)
- Latest version is always the highest version number

### Storage

- Upload generated file to Supabase Storage: `{firm_id}/{project_id}/generated/CMA_{name}_v{n}.xlsx`
- Create row in `generated_files` table with file_name, storage_path, version, file_size

### Temp File Cleanup

- Use Python's `tempfile` module for intermediate files
- Clean up temp files after upload to storage
- Never leave temp files around

---

## What NOT to Do

- Don't generate if validation has errors (unless explicitly skipped)
- Don't overwrite previous versions
- Don't modify the original template file
- Don't expose temp file paths to the user
- Don't generate for projects in 'draft' or 'extracting' status

---

## Verification

- [ ] Generate with valid data → Excel file created, uploaded to Storage
- [ ] File name follows convention
- [ ] Version increments: first generation = v1, second = v2
- [ ] `generated_files` table has the record
- [ ] Validation errors → generation blocked, errors returned
- [ ] Validation warnings only → generation proceeds, warnings included
- [ ] Project status updated to 'completed'
- [ ] pipeline_progress = 100
- [ ] Temp files cleaned up after generation
- [ ] Generated file downloadable via signed URL (from Phase 03 task 3.6)

---

## Done → Move to task-6.6-generation-endpoint.md
