import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CategorySelectorComponent } from './category-selector';

describe('CategorySelectorComponent', () => {
  let component: CategorySelectorComponent;
  let fixture: ComponentFixture<CategorySelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CategorySelectorComponent]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CategorySelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render category options', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const checkboxes = compiled.querySelectorAll('input[type="checkbox"]');
    expect(checkboxes.length).toBe(component.categories.length);
  });
});
