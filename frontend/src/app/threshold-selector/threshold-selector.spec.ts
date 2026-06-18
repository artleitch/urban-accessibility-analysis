import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ThresholdSelectorComponent } from './threshold-selector';

describe('ThresholdSelectorComponent', () => {
  let component: ThresholdSelectorComponent;
  let fixture: ComponentFixture<ThresholdSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ThresholdSelectorComponent]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ThresholdSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render threshold options', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const options = compiled.querySelectorAll('option');
    expect(options.length).toBe(6);
  });
});
